{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
PROPERTY bufferSize : DWORD
!__GETTER__!
//This gets the amount of bytes in the buffer
// | 1         | NSN      | 22-06-20 | Creation
VAR
END_VAR

!__IMPLEMENTATION__!
bufferSize		:=		bufferPosition - bufferAddress;
!__SETTER__!
