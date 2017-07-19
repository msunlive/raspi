<?php
/*------------------------------------------------------
 读取log最后几行
--------------------------------------------------------*/
error_reporting(0); //抑制所有错误信息
@header("content-Type: text/html; charset=utf-8"); //语言强制
ob_start();
date_default_timezone_set('Asia/Shanghai');//此句用于消除时间差

$stime=microtime(true); 
$ALL_SIZE = 10240;
/**
 * 取文件最后$n行
 * @param string $filename 文件路径
 * @param int $n 最后几行
 * @return mixed false表示有错误，成功则返回字符串
 */
function FileLastLines($filename,$n){
	global $ALL_SIZE;
	
	$input_n = $n;
    if(!$fp=fopen($filename,'r')){
        echo "打开文件失败";
        return false;
    }
    
    $pos=-2;
    $eof="";
    $str="";
    while($n>0){
        while($eof!="\n"){
            if(!fseek($fp,$pos,SEEK_END)){
                $eof=fgetc($fp);
                $pos--;
            }else{
                break;
            }
        }
        $str.=fgets($fp);
        $eof="";
        $n--;
    }
    
    if($str == "") {
        if(filesize($filename) < $ALL_SIZE) {
            return file_get_contents($filename);
        }else {
            return "文件超过{$ALL_SIZE}B，但没有{$input_n}行";
        }
    }
    
    return $str;
}
?>
<html>
    <head>
        <meta http-equiv="refresh" content="5" />
    </head>
    <body style="font-family:MONACO,Consolas;font-size: 20px;">
        <div>
            <?php echo nl2br(FileLastLines('py/g5/log.txt',20)); ?>
        </div>
        <div style="font-size: 12px;">
            <?php 
                $etime = microtime(true);//获取程序执行结束的时间
                $total = $etime - $stime;   //计算差值
                $ntime = date('Y-m-d H:i:s',time());
                echo "<hr />当前时间: {$ntime}<br />执行时间: {$total}秒";
            ?>
        </div>
    </body>
</html>