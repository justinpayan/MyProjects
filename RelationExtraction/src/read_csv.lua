#!/usr/bin/env th
require 'torch'
require 'dp'
-- Read CSV file

-- Split string
function string:split(sep)
  local sep, fields = sep, {}
  local pattern = string.format("([^%s]+)", sep)
  self:gsub(pattern, function(substr) fields[#fields + 1] = substr end)
  return fields
end

local maxNumWords = tonumber(arg[4])
--print(maxNumWords)
local filePath = arg[1]

-- Count number of rows and columns in file
local i = 0
for line in io.lines(filePath) do
  if i == 0 then
    COLS = #line:split('\t')
  end
  i = i + 1
end

local ROWS = i - 1  -- Minus 1 because of header

-- Read data from CSV to tensor
local csvFile = io.open(filePath, 'r')
local header = csvFile:read()

local dataset={};
local annotation={}
function dataset:size() return ROWS end -- should actually return the size of the dataset

local i = 0
for line in csvFile:lines('*l') do
  i = i + 1
    local singleLine = line:split('\t')
  local inputt = torch.Tensor(singleLine)
  --print(COLS)
  --print(inputt:size())
    input = inputt:narrow(1,1,COLS-3)
    local output = inputt:narrow(1,COLS-2,1)
    local metadata = inputt:narrow(1,COLS-1,2)
    if arg[3] == 'appendToEnd' then
        input = input:resize(maxNumWords+56,108) -- sentences can be up to length maxNumWords, and we
                                                 -- append 6000 wn features to the end
    else
        input = input:resize(maxNumWords,208)
    end
    --print(input)
    --print(output)
    if i%100 == 0 then
        print(i)
    end
    dataset[i] = {input, output}
    annotation[i] = {metadata}
end

csvFile:close()

-- Serialize tensor
local outputFilePath = arg[2]
torch.save(outputFilePath, dataset)
torch.save('annotationTest.th7',annotation)

-- Deserialize tensor object
--local restored_data = torch.load(outputFilePath)

-- Make test
print(dataset:size())
--print(restored_data:size())