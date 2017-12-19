require 'dp'
ds = dp.Mnist()

trainInputs = ds:get('train','inputs','bchw')
trainInputs = trainInputs:narrow(1,1,1000)
trainTargets = ds:get('train','targets','b')
trainTargets = trainTargets:narrow(1,1,1000)
validInputs = ds:get('valid','inputs','bchw')
validInputs = validInputs:narrow(1,1,200)
validTargets = ds:get('valid','targets','b')
validTargets = validTargets:narrow(1,1,200)

module = nn.Sequential()
module:add(nn.Convert('bchw','bf'))
module:add(nn.Linear(1*28*28,200))
module:add(nn.Tanh())
module:add(nn.Linear(200,200))
module:add(nn.Tanh())
module:add(nn.Linear(200,10))
module:add(nn.LogSoftMax())

print(5)

criterion = nn.ClassNLLCriterion()

-- Single epoch of training
require 'dpnn'
function trainEpoch(module,criterion, inputs,targets)
print(inputs:size(1))
for i=1,inputs:size(1) do
print(i)
local idx = math.random(1,inputs:size(1))
local input, target = inputs[idx],targets:narrow(1,idx,1)
local output = module:forward(input)
local loss = criterion:forward(output,target)
local gradOutput = criterion:backward(output,target)
module:zeroGradParameters()
local gradInput = module:backward(input,gradOutput)
module:updateGradParameters(0.9)
module:updateParameters(0.1)
end
end



-- Validate against the validation data set

require 'optim'
cm = optim.ConfusionMatrix(10)
function classEval(module, inputs, targets)
cm:zero()
for idx=1,inputs:size(1) do
local input, target = inputs[idx], targets[idx]
--print(target)
--print(nnet:forward(input))
local output = module:forward(input)
--print(output)
cm:add(output,target)
end
cm:updateValids()
return cm.totalValid
end


-- Training Loop

bestAccuracy, bestEpoch = 0,0
wait = 0
for epoch = 1,300 do
trainEpoch(module, criterion, trainInputs, trainTargets)
local validAccuracy = classEval(module, validInputs, validTargets)
print(validAccuracy)
print(bestAccuracy)
if validAccuracy > bestAccuracy then
bestAccuracy, bestEpoch = validAccuracy, epoch
torch.save("savednnet", module)
print(string.format("new max: %f @ %f", bestAccuracy, bestEpoch))
wait = 0
else
wait = wait + 1
print(wait)
if wait > 30 then break end
end
end

-- build a convnet
require 'dp'
require 'optim'
require 'dpnn'

cnn = nn.Sequential()
cnn:add(nn.Convert('bhwc','bchw'))
cnn:add(nn.SpatialConvolution(1,16,5,5,1,1,2,2))
cnn:add(nn.ReLU())
cnn:add(nn.SpatialMaxPooling(2,2,2,2))
cnn:add(nn.SpatialConvolution(16,32,5,5,1,1,2,2))
cnn:add(nn.ReLU())
cnn:add(nn.SpatialMaxPooling(2,2,2,2))
cnn:add(nn.Collapse(3))
cnn:add(nn.Linear(1568,200))
cnn:add(nn.ReLU())
cnn:add(nn.Linear(200,10))
cnn:add(nn.LogSoftMax())

train = dp.Optimizer{
loss = nn.ModuleCriterion(nn.ClassNLLCriterion(), nil, nn.Convert()),
callback = function(model, report)
model:updateGradParameters(0.9) -- momentum
model:updateParameters(0.1) -- learning rate
model:maxParamNorm(2) -- max norm constraint on weight matrix rows
model:zeroGradParameters()
end,
feedback = dp.Confusion(), -- wraps optim.ConfusionMatrix
sampler = dp.ShuffleSampler{batch_size = 32}, 
progress = true
}
valid = dp.Evaluator{
feedback = dp.Confusion(), sampler = dp.Sampler{batch_size = 32}
}
test = dp.Evaluator{
feedback = dp.Confusion(), sampler = dp.Sampler{batch_size = 32}
}

xp = dp.Experiment{
model = cnn,
optimizer = train, validator = valid, tester = test,
observer = dp.EarlyStopper{
error_report = {'validator','feedback','confusion','accuracy'},
maximize = true, max_epochs = 50 
},
random_seed = os.time(), max_epoch = 2000
}

require 'cutorch'
require 'cunn'
xp:cuda()
