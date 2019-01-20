import React, { Component } from 'react'
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import FormLabel from '@material-ui/core/FormLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import FormControl from '@material-ui/core/FormControl';
import { PieChart, 
    Pie, 
    Sector, 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip,
    Legend,
    Cell
   } from 'recharts'

export default class WykresyKolowe extends Component {
    
    state= {
        value: 0,
        activeIndex: 0,
        type: 'train'
    }

    handleChange = (event, value) => {
        this.setState({ value });
      };

      onPieEnter(data, index) {
        this.setState({
          activeIndex: index
        })
      }
      handleTypeChange = event => {
		this.setState({ type: event.target.value });
	  }
    render(){
        const colors = ['#801515', '#D46A6A', '#AA3939', '#550000']
        const renderActiveShape = (props) => {
            const RADIAN = Math.PI / 180;
            const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle,
              fill, payload, percent, value } = props;
            const sin = Math.sin(-RADIAN * midAngle);
            const cos = Math.cos(-RADIAN * midAngle);
            const sx = cx + (outerRadius + 10) * cos;
            const sy = cy + (outerRadius + 10) * sin;
            const mx = cx + (outerRadius + 30) * cos;
            const my = cy + (outerRadius + 30) * sin;
            const ex = mx + (cos >= 0 ? 1 : -1) * 22;
            const ey = my;
            const textAnchor = cos >= 0 ? 'start' : 'end';
          
            return (
              <g>
                <text style={{ fontFamily: 'Roboto, sans-serif' }} x={cx} y={cy} dy={8} textAnchor="middle" fill={fill}>{payload.name}</text>
                <Sector
                  cx={cx}
                  cy={cy}
                  innerRadius={innerRadius}
                  outerRadius={outerRadius}
                  startAngle={startAngle}
                  endAngle={endAngle}
                  fill={fill}
                />
                <Sector
                  cx={cx}
                  cy={cy}
                  startAngle={startAngle}
                  endAngle={endAngle}
                  innerRadius={outerRadius + 6}
                  outerRadius={outerRadius + 10}
                  fill={fill}
                />
                <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none"/>
                <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none"/>
                <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#333">{`${value}`}</text>
                <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} dy={18} textAnchor={textAnchor} fill="#999">
                  {`(${(percent * 100).toFixed(2)}%)`}
                </text>
              </g>
            );
          }

        return(
            <div>
                <Tabs
                    value={this.state.value}
                    onChange={this.handleChange}
                    indicatorColor="primary"
                    textColor="primary"
                    scrollable
                    scrollButtons="auto"
                    style={{backgroundColor: 'black', marginBottom: 10}}
                    >
                        <Tab label='Użytkownicy' />
                        {
                            this.props.tagCount.map((tag, id)=>
                                <Tab label={tag.tagName} />
                            )
                        }
                    </Tabs>
                    {this.state.value === 0 &&
                    <div style={{
                        backgroundColor: 'black',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center'
                        }}>
                        <FormControl component="fieldset">
                                <FormLabel component="legend">Wybierz typ nagrania:</FormLabel>
                                <RadioGroup
                                    value={this.state.type}
                                    onChange={this.handleTypeChange}
                                    style={{flexDirection: 'row', alignItems: 'center'}}
                                >
                                    <FormControlLabel value="train" control={<Radio />} label="Trenowanie" />
                                    <FormControlLabel value="test" control={<Radio />} label="Test" />
                                </RadioGroup>
                        </FormControl>
                        <PieChart width={350} height={300}>
                            <Pie 
                                dataKey='value'
                                activeIndex={this.state.activeIndex}
                                activeShape={renderActiveShape} 
                                data={this.state.type === 'train'? this.props.userSoundsTrainCount: this.props.userSoundsTestCount} 
                                cx={160} 
                                cy={150} 
                                innerRadius={60}
                                outerRadius={80} 
                                fill="rgb(100,100,100)"
                                onMouseEnter={this.onPieEnter.bind(this)}
                                >
                                {
                                    this.props.userSoundsTrainCount.map((entry, index) => <Cell fill={colors[index%4]}/>)
                                }
                                </Pie>
                        </PieChart>
                        <BarChart width={500} height={300} data={this.state.type === 'train'? this.props.userSoundsTrainCount: this.props.userSoundsTestCount}
                                margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                            <CartesianGrid strokeDasharray="3 3"/>
                            <XAxis dataKey="name" style={{ fontFamily: 'Roboto, sans-serif' }}/>
                            <YAxis />
                            <Tooltip/>
                            <Legend />
                            <Bar dataKey="value">
                            {
                                (this.state.type === 'train'? this.props.userSoundsTrainCount: this.props.userSoundsTestCount).map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={colors[index%4]}/>
                                ))
                            }
                            </Bar>
                        </BarChart>
                    </div>
                    }
                    {
                        this.props.tagReady && this.props.tagCount.map((tag, id)=>
                            this.state.value === id+1 &&
                            <div style={{
                                backgroundColor: 'black',
                                display: 'flex',
                                justifyContent: 'center'
                                }}>
                                <PieChart width={650} height={300}>
                                    <Pie 
                                        dataKey='value'
                                        activeIndex={this.state.activeIndex}
                                        activeShape={renderActiveShape} 
                                        data={tag.values} 
                                        cx={320} 
                                        cy={150} 
                                        innerRadius={60}
                                        outerRadius={80} 
                                        fill="rgb(100,100,100)"
                                        onMouseEnter={this.onPieEnter.bind(this)}
                                        >
                                        {
                                            tag.values.map((entry, index) => <Cell fill={colors[index%4]}/>)
                                        }
                                        </Pie>
                                </PieChart>
                                <BarChart width={600} height={300} data={tag.values}
                                        margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                                    <CartesianGrid strokeDasharray="3 3"/>
                                    <XAxis dataKey="name" style={{ fontFamily: 'Roboto, sans-serif' }}/>
                                    <YAxis/>
                                    <Tooltip/>
                                    <Legend />
                                    <Bar dataKey="value">
                                    {
                                        tag.values.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={colors[index%4]}/>
                                        ))
                                    }
                                    </Bar>
                                </BarChart>
                            </div>
                        )
                    }
                    }
            </div>
        )
    }
}