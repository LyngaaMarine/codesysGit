{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
//This returns the current index position in the array
PROPERTY arrayIndex : WORD
!__GETTER__!
VAR
END_VAR

!__IMPLEMENTATION__!
arrayIndex			:=		reader.arrayIndex;
!__SETTER__!
