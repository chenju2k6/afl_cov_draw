fuzzer=$1
round=$2
for (( i=1; i<=$round; i++ )); do
	echo $i
docker cp ${fuzzer}_nm${i}:/out/corpus ${fuzzer}_nm${i}
docker cp ${fuzzer}_readelf${i}:/out/corpus ${fuzzer}_readelf${i}
docker cp ${fuzzer}_objdump${i}:/out/corpus ${fuzzer}_objdump${i}
docker cp ${fuzzer}_size${i}:/out/corpus ${fuzzer}_size${i}
docker cp ${fuzzer}_tcpdump${i}:/out/corpus ${fuzzer}_tcpdump${i}
docker cp ${fuzzer}_tiff2pdf${i}:/out/corpus ${fuzzer}_tiff2pdf${i}
docker cp ${fuzzer}_libarchive${i}:/out/corpus ${fuzzer}_libarchive${i}
done
