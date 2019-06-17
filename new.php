$post['files'] =$_FILES['image'];
//return $post;
$filename = basename($finder->image);
$filedata = $_FILES['image']['tmp_name'];
$filesize = $_FILES['image']['size'];
// Create a CURLFile object
//$cfile ="@".public_path('finder_image/'.basename($finder->image)).";filename=".basename($finder->image).";type=".$request->image->getClientOriginalExtension()."";
// $cfile =new CURLFile(public_path('finder_image/'.basename($finder->image)),$request->image->getClientOriginalExtension(),basename($finder->image));
// $data = array('file' => $cfile);
$file = new \CURLFile(''.public_path('finder_image/'.basename($finder->image)),'image/jpeg',basename($finder->image)); //<-- Path could be relative
$data = array('name' => 'file', 'file' => $file);
//   $data = array(
//     'file' => '@' . public_path('finder_image/'.basename($finder->image))
// );
$curl = curl_init();
curl_setopt_array($curl, array(
  CURLOPT_PORT => "5000",
  CURLOPT_URL => "http://localhost:5000/api/detect_image",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => "",
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => "POST",
  CURLOPT_POSTFIELDS => $data,
  CURLOPT_HTTPHEADER => array(
    "cache-control: no-cache",
    "content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"
  ),
));
$info = curl_getinfo($curl);
//return $info;
$response = curl_exec($curl);
$err = curl_error($curl);

curl_close($curl);

if ($err) {
  return  "cURL Error #:" . $err;
} else {
  return $response;
}
