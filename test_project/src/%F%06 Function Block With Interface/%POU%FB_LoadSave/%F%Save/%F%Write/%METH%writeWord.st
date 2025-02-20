{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
//This adds a value data to the buffer
// |**Version**|**Author**| **Date** |**Changes** 
// | 1         | NSN      | 16-05-21 | Creation
METHOD writeWord
VAR_INPUT
	value			:WORD;
END_VAR
!__IMPLEMENTATION__!
writer.writeWord(value:=value);
logChange(valPoint:=ADR(value),valType:=ESysType.tWORD);