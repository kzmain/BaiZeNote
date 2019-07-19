//封装document.querySelector
let docGet = function(selector){
  return document.querySelector(selector);
};
let calcStartTime = function () {//计算开始绘制日期
  let today_date = new Date();
  let oneDay = 1000 * 60 * 60 * 24;
  let day = today_date.getDay();//day=星期几
  let startTime = new Date(today_date.getTime() - oneDay * (7 * 52 + day))
  return startTime;
}
//格式化输出时间
let getFormatTime = function (date) {//date为日期对象
  return date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
}

//总共需要绘制天数 ：((new Date()-startTime)/oneDay) + 1
//计算该天为绘制的第几天,从0开始计数
let calcDay = function (date, startTime) {//两个参数均为日期对象
  let oneDay = 1000 * 60 * 60 * 24;
  return parseInt((date - startTime) / oneDay)
}

let getContributionsArray = function () {//解析json字符串，返回记录了一年内每天贡献次数的数组
  let startTime = calcStartTime()
  let data_count_arr = new Array(371)
  for (var section in json) {
    for (var note in json[section]['NOTES_DICT']) {
      for (var time_num in json[section]['NOTES_DICT'][note]['NOTE_MODIFICATION_TIME']) {
        let time = json[section]['NOTES_DICT'][note]['NOTE_MODIFICATION_TIME'][time_num]
        let thatTime = new Date(time);
        let thatDay = calcDay(thatTime, startTime)
        if (data_count_arr[thatDay] == undefined) {
          data_count_arr[thatDay] = 1;
        }
        else {
          data_count_arr[thatDay]++;
        }
      }

    }
  }
  return data_count_arr;
}
let createTagSvg = function () {
  let svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute("style", "float: right;");
  svg.setAttribute("width", "712")
  svg.setAttribute("height", "112")
  return svg;
}
let createTagG = function (translate_x) {
  let g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  let transfrom_value = "translate(" + translate_x + ", 0)"
  g.setAttribute("transform", transfrom_value)
  return g;
}
let createTagRect = function (x, y, color, data_acount, data_date) {
  let rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  rect.setAttribute("class", "day")
  rect.setAttribute("width", "10")
  rect.setAttribute("height", "10")
  rect.setAttribute("x", x)
  rect.setAttribute("y", y)
  rect.setAttribute("fill", color)
  rect.setAttribute("data-count", data_acount)
  rect.setAttribute("data-date", data_date)
  return rect;
}
let createTagText = function (x, month) {
  let text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute("fill", "#9E9E9E")
  text.setAttribute("x", x);
  text.setAttribute("y", "107.5");
  text.innerHTML = month
  return text;
}
let drawContributions = function () {
  //时间相关
  let startTime = calcStartTime()
  let oneDay = 1000 * 60 * 60 * 24;//定义一天时长，方便后边运算
  let days_num = ((new Date() - startTime) / oneDay) + 1;//总共需要绘制天数
  let thatDay = startTime;//正在绘制的那天，date对象
  let thatDayFormat;//thatDay的格式化日期
  let lastMonth = thatDay.getMonth();
  let thisMonth = lastMonth + 1
  
  //标签
  let svg = createTagSvg();//svg标签
  let g;//g标签

  //绘制相关
  let text_arr = new Array(12);
  let color = ["#ebedf0", "#c6e48b", "#7bc96f", "#239a3b", "#196127"];//不同更新程度的颜色
  let rect_color;//当前rect的颜色
  let y_arr = ["0", "13", "26", "39", "52", "65", "78"];//y的竖直位置列表
  let rect_x = 14;//rect的水平位置
  let rect_y;//rect的竖直位置
  let g_trans_x = 0;//g的水平位置
  let contributionsArray = getContributionsArray()//获取一年contributions次数的数组
  
  //开始绘制
  for (var i = 0; i < days_num; i++) {
    thatDay = new Date(startTime.getTime() + i * (oneDay))
    thatDayFormat = getFormatTime(thatDay)
    rect_y = y_arr[i % 7];

    switch (contributionsArray[i]) {//设置颜色
      case undefined: rect_color = color[0]; break;
      case 1:
      case 2:
      case 3: rect_color = color[1]; break;
      case 4:
      case 5: rect_color = color[2]; break;
      case 6:
      case 7:
      case 8:
      case 9:
      case 10: rect_color = color[3]; break;
      default: rect_color = color[4]; break;
    }
    if (i % 7 == 0) {//每个g只放7个rect
      g = createTagG(g_trans_x);
      svg.appendChild(g);
      rect_x--;
      g_trans_x += 14//g位移
      
      thisMonth = thatDay.getMonth() + 1;
      if (lastMonth != thisMonth) {//创建底部月份
        text_arr.push(createTagText(parseInt(i / 7) * 13 + 14, thisMonth)) //先保存，最后append
        lastMonth = thisMonth;
      }
    }
    if (contributionsArray[i] == undefined) {
      g.appendChild(createTagRect(rect_x, rect_y, rect_color, 0, thatDayFormat))
    }
    else {
      g.appendChild(createTagRect(rect_x, rect_y, rect_color, contributionsArray[i], thatDayFormat))
    }
  }
  for (var text in text_arr) {
    svg.appendChild(text_arr[text])
  }
  docGet(".contributions").appendChild(svg);
}
let json = {
  ".": {
    "REL_PATH": ".",
    "SECTION_NAME": "\ud83d\udcdaHead_First_Data_Analysis_2009",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:48:00 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:48:00 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {
      "0": "Intro",
      "1": "+ Module",
      "2": "+ Write own Module",
      "3": ".idea"
    },
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "Intro",
        "NOTE_FILE_PATH": "Intro.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Wed Jul 10 08:24:22 2019",
        "NOTE_MODIFICATION_TIME": [
          "Wed Jul 10 08:24:22 2019"
        ]
      },
      "1": {
        "NOTE_FILE_NAME": "\u996e\u98df\u4e60\u60ef",
        "NOTE_FILE_PATH": "\u996e\u98df\u4e60\u60ef.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Wed Jul 10 08:25:07 2019",
        "NOTE_MODIFICATION_TIME": [
          "Wed Jul 10 08:25:07 2019"
        ]
      },
      "2": {
        "NOTE_FILE_NAME": "\u81b3\u98df\u642d\u914d",
        "NOTE_FILE_PATH": "\u81b3\u98df\u642d\u914d.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Wed Jul 10 08:24:42 2019",
        "NOTE_MODIFICATION_TIME": [
          "Wed Jul 10 08:24:42 2019"
        ]
      }
    }
  },
  "Intro": {
    "REL_PATH": "Intro",
    "SECTION_NAME": "Intro",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:48:00 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:48:00 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "Intro",
        "NOTE_FILE_PATH": "Intro/Intro.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 19:38:08 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jun 11 19:38:08 2019"
        ]
      },
      "1": {
        "NOTE_FILE_NAME": "\u996e\u98df\u4e60\u60ef",
        "NOTE_FILE_PATH": "Intro/\u996e\u98df\u4e60\u60ef.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jul  9 15:25:03 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jul  9 15:25:03 2019"
        ]
      }
    }
  },
  "+ Module": {
    "REL_PATH": "+ Module",
    "SECTION_NAME": "+ Module",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:47:26 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:47:26 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {
      "0": "+ Module/1.Data Analysis procedure"
    },
    "NOTES_DICT": {}
  },
  "+ Module/1.Data Analysis procedure": {
    "REL_PATH": "+ Module/1.Data Analysis procedure",
    "SECTION_NAME": "1.Data Analysis procedure",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:48:00 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:48:00 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {
      "0": "+ Module/1.Data Analysis procedure/1. Define the problem",
      "1": "+ Module/1.Data Analysis procedure/2. Disassemble",
      "2": "+ Module/1.Data Analysis procedure/3. Evaluate",
      "3": "+ Module/1.Data Analysis procedure/4. Decide"
    },
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "Data Analysis procedure",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/Data Analysis procedure.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 00:13:23 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jun 11 00:13:23 2019"
        ]
      },
      "1": {
        "NOTE_FILE_NAME": "Sharpen_Your_Pencil_P55",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/Sharpen_Your_Pencil_P55.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Fri Jun 28 14:06:33 2019",
        "NOTE_MODIFICATION_TIME": [
          "Fri Jun 28 14:06:33 2019"
        ]
      },
      "2": {
        "NOTE_FILE_NAME": "Sharpen_Your_Pencil_P47",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/Sharpen_Your_Pencil_P47.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 00:13:23 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jun 11 00:13:23 2019"
        ]
      },
      "3": {
        "NOTE_FILE_NAME": "Sharpen_Your_Pencil_P52",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/Sharpen_Your_Pencil_P52.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 00:13:23 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jun 11 00:13:23 2019"
        ]
      }
    }
  },
  "+ Module/1.Data Analysis procedure/1. Define the problem": {
    "REL_PATH": "+ Module/1.Data Analysis procedure/1. Define the problem",
    "SECTION_NAME": "1. Define the problem",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:48:00 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:48:00 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "1. Define the problem",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/1. Define the problem/1. Define the problem.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 00:13:23 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jun 11 00:13:23 2019"
        ]
      }
    }
  },
  "+ Module/1.Data Analysis procedure/2. Disassemble": {
    "REL_PATH": "+ Module/1.Data Analysis procedure/2. Disassemble",
    "SECTION_NAME": "2. Disassemble",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:48:00 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:48:00 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "2. Disassemble",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/2. Disassemble/2. Disassemble.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 00:13:23 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jun 11 00:13:23 2019"
        ]
      }
    }
  },
  "+ Module/1.Data Analysis procedure/3. Evaluate": {
    "REL_PATH": "+ Module/1.Data Analysis procedure/3. Evaluate",
    "SECTION_NAME": "3. Evaluate",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:48:00 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:48:00 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "3. Evaluate",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/3. Evaluate/3. Evaluate.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 00:13:23 2019",
        "NOTE_MODIFICATION_TIME": [
          "Tue Jun 11 00:13:23 2019"
        ]
      }
    }
  },
  "+ Module/1.Data Analysis procedure/4. Decide": {
    "REL_PATH": "+ Module/1.Data Analysis procedure/4. Decide",
    "SECTION_NAME": "4. Decide",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Fri Jul 12 21:54:21 2019",
    "SECTION_UPDATE_TIME": [
      "Fri Jul 12 21:54:21 2019",
      "Fri Jul 12 21:54:43 2019",
      "Fri Jul 12 21:56:50 2019",
      "Fri Jul 12 22:00:16 2019",
      "Fri Jul 12 22:39:19 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {
      "0": "+ Module/1.Data Analysis procedure/4. Decide/1. Define the problem",
      "1": "+ Module/1.Data Analysis procedure/4. Decide/2. Disassemble",
      "2": "+ Module/1.Data Analysis procedure/4. Decide/3. Evaluate"
    },
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "4",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/4. Decide/4. Decide.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 00:13:23 2019",
        "NOTE_MODIFICATION_TIME": [
          "Thu May 23 00:33:23 2019",
          "Tue Jun 11 00:13:23 2019"
        ]
      }
    }
  },
  "+ Module/1.Data Analysis procedure/4. Decide/1. Define the problem": {
    "REL_PATH": "+ Module/1.Data Analysis procedure/4. Decide/1. Define the problem",
    "SECTION_NAME": "1. Define the problem",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Fri Jul 12 21:54:21 2019",
    "SECTION_UPDATE_TIME": [
      "Fri Jul 12 21:54:21 2019",
      "Fri Jul 12 21:54:43 2019",
      "Fri Jul 12 21:56:50 2019",
      "Fri Jul 12 22:00:16 2019",
      "Fri Jul 12 22:39:19 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "1",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/4. Decide/1. Define the problem/1. Define the problem.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 17:14:15 2019",
        "NOTE_MODIFICATION_TIME": [
          "Wed May 22 11:02:09 2019",
          "Tue Jun 11 17:14:15 2019"
        ]
      }
    }
  },
  "+ Module/1.Data Analysis procedure/4. Decide/2. Disassemble": {
    "REL_PATH": "+ Module/1.Data Analysis procedure/4. Decide/2. Disassemble",
    "SECTION_NAME": "2. Disassemble",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Fri Jul 12 21:54:21 2019",
    "SECTION_UPDATE_TIME": [
      "Fri Jul 12 21:54:21 2019",
      "Fri Jul 12 21:54:43 2019",
      "Fri Jul 12 21:56:50 2019",
      "Fri Jul 12 22:00:16 2019",
      "Fri Jul 12 22:39:26 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "2",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/4. Decide/2. Disassemble/2. Disassemble.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 17:14:15 2019",
        "NOTE_MODIFICATION_TIME": [
          "Wed May 29 12:40:08 2019",
          "Tue Jun 11 17:14:15 2019"
        ]
      }
    }
  },
  "+ Module/1.Data Analysis procedure/4. Decide/3. Evaluate": {
    "REL_PATH": "+ Module/1.Data Analysis procedure/4. Decide/3. Evaluate",
    "SECTION_NAME": "3. Evaluate",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Fri Jul 12 21:54:21 2019",
    "SECTION_UPDATE_TIME": [
      "Fri Jul 12 21:54:21 2019",
      "Fri Jul 12 21:54:43 2019",
      "Fri Jul 12 21:56:50 2019",
      "Fri Jul 12 22:00:16 2019",
      "Fri Jul 12 22:39:26 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "3",
        "NOTE_FILE_PATH": "+ Module/1.Data Analysis procedure/4. Decide/3. Evaluate/3. Evaluate.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Tue Jun 11 17:14:15 2019",
        "NOTE_MODIFICATION_TIME": [
          "Wed May 22 16:08:31 2019",
          "Tue Jun 11 17:14:15 2019"
        ]
      }
    }
  },
  "+ Write own Module": {
    "REL_PATH": "+ Write own Module",
    "SECTION_NAME": "+ Write own Module",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Sat Jul 13 20:48:00 2019",
    "SECTION_UPDATE_TIME": [
      "Sat Jul 13 20:48:00 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {
      "0": {
        "NOTE_FILE_NAME": "__mian__ function",
        "NOTE_FILE_PATH": "+ Write own Module/__mian__ function.md",
        "NOTE_FILE_TYPE": ".md",
        "NOTE_REFERENCES": {},
        "NOTE_LOCK": false,
        "NOTE_HIDE": false,
        "NOTE_TAG": [],
        "NOTE_CREATION_TIME": "Wed Jun 12 03:01:44 2019",
        "NOTE_MODIFICATION_TIME": [
          "Wed Jun 12 03:01:44 2019"
        ]
      }
    }
  },
  ".idea": {
    "REL_PATH": ".idea",
    "SECTION_NAME": ".idea",
    "SECTION_LOCK": false,
    "SECTION_HIDE": false,
    "SECTION_TAG": [],
    "SECTION_CREATION_TIME": "Fri Jul 12 19:27:14 2019",
    "SECTION_UPDATE_TIME": [
      "Fri Jul 12 19:27:14 2019",
      "Sat Jul 13 22:09:20 2019"
    ],
    "SUB_SECTION_REL_PATH_DICT": {},
    "NOTES_DICT": {}
  }
}
drawContributions();
