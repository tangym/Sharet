# Sharet
Share files easily. No need for database.

## Usage
TODO

## Instruction
### Configuration
`Sharet.conf` uses json format to configure the program.

### Backup File
The program uses backup file configured in `Sharet.conf` to record file routes.
When the program starts, it reads the file first and recovers routes in the backup file.

- check whether backup file matches files in share directory 
  - remove the records that does not in share directory
  - when a file in share directory is recorded, check whether it has been renamed
  - when a file in share directory is not recorded, move it to upload directory 
- record files in upload directory and rename & move to share directory
  - a file has the same md5 as a file in share directory: delete this file in upload directory



```

---------------------------------
```


```json
[
  {
    "name": "file1.name",
    "route": "/file1/route",
    "md5": "9e107d9d372bb6826bd81d3542a419d6",
  },
  {
    "name": "file2.name",
    "route": "/file2/route",
    "md5": "d41d8cd98f00b204e9800998ecf8427e",
  },
]
```


- md5-file
- route-file
- route-passwd

