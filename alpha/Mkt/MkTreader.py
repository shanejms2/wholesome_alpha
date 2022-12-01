import pandas as pd
import yfinance as yf
import warnings


class MkTreader:
    """ 
    Collect historical market prices from market data providers such as
    'yahoo', 'eodhistoricaldata', 'alphavantage' and 'marketstack'.
    
    Public function members:
        - `get` : returns the historical time series requested
        - `get_request_status` : returns info about the request status
        - `get_error_log` : returns the list of missing dates in the \
            time series
    Public data members:
        - `dsource` : dict of request instructions per symbol
        - `delta_time` : execution time of the request in seconds
        - `rout` : pandas.DataFrame contenig historical prices for all \
            symbols. It is created during the call of `get` function.
        - `rout_status` : request status information. It is created during \
            the call of `get_request_status` function or during the \
            call of function `get` with option `verbose=True`.
        - `error_log` : contains lists of missing historical observation \
            dates. It is created together with `rout_status`.
    """
    def __init__(self):
        '''
        Constructor
        '''
        self.dsource = None
        self.delta_time = None
        self.rout = None
        self.rout_status = None
        self.error_log = None
        
        self.sdate = None
        self.edate = None
        
        self._bday = None
        
        self._col = ['open', 'high', 'low', 'close', 'volume', 'adjusted', 
                     'divd', 'split']
        self._out_col = ['symbol'] + self._col + ['source', 'recordDate']
        self._alphavantage_max_req_per_min = 5

        def get(self, symbol=[], sdate="2012-01-01", edate='today', calendar=None,
            output_format='frame', source=None, force=False, save=True,
            file_dir="outDir", file_format='csv', api_key=None, param=None,  
            verbose=True):        
            '''
            Get MkT data for a set of stock symbols.
        
            Collect historical stock prices from various market data providers 
            such as yahoo, alphavantage, eodhistoricaldata and marketstack as
            well as form saved data in local files.
        
            Parameters
            ----------
            `symbol` : str or list of str, optional
                Stock symbols to be uploaded.
                The default is `[]`.
            `sdate` : date, optional
                The start date of historical time series.
                The default is `"2012-01-01"`.
            `edate` : date, optional
                The end date of historical time series (must: sdate >= edate)
                The default is `'today'`.
            `calendar` : `numpy.busdaycalendar`, optional
                Exchange business day calendar. If set to `None` it will default to 
                the NY stock exchange business calendar (provided by the azapy 
                function NYSEgen).
                The default is `None`.
            `output_format` : str, optional
                The function output format. It can be:
                
                - `'frame'` - pandas.DataFrame
                - `'dict'` - dict of pandaws.DataFrame where the keys are the \
                    symbols. 
                
                The default is `'frame'`
            `source` : str or dict, optional
                If it is a str, then it represents the market data provider for all
                historical prices requests. Possible values are: 'yahoo', 
                'alphavantage', 'alphavantage_yahoo', 'eodhistoricaldata',
                'eodhistoricaldata_yahoo' and 'marketstack'. If set to `None` 
                it will default to `'yahoo'`.
                
                It can be set to a dictionary containing specific instructions for 
                each stock symbol. 
                The dict keys are stock symbols. The values are dict's of 
                instructions. Valid keys for the instructions dict are the names of
                this function call variables except 'sdate', 'edate', 'calendar'
                and 'output_format'. 
                The actual set of stock symbols is given by the union 
                of variable 'symbol' and the keys of the dict 'source'. Missing  
                values in the symbol instruction dict's will be filled with the 
                values of the function call variables. 
                The values of the function call variables act as 
                generic values to be used in absence of specific instructions 
                in the 'source' dict. 
                The default is `None`.
                
                Example of dict 'source': 
                    
                source = \
                    {'AAPL': {'source': 'eodhistoricaldata, 'verbose': `True`}, \
                    'SPY': {'source': 'yahoo', 'force': `True`}}
                    
                In this case there are 2 symbols that will be added (union) to 
                the set of symbols defined by 'symbol' variable. For symbol 'AAPL' 
                the provider source is eodhistoricaldata and the 'verbose' 
                instruction 
                is set to `True`. The rest of the instructions: 'force', 'save',
                'file_dir', 'file_format', 'api_key' and 'param' are set 
                to the values of the corresponding function call variables.
                Similar for symbol 'SPY'. The instructions for the rest of the 
                symbols that may be specified in the 'symbol' variable will be
                set according to the values of the function call variables.
            `force` : Boolean, optional
                - `True`: will try to collect historical prices exclusive from  \
                the market data providers.
                - `False`: first it will try to load the historical \
                prices form a local saved file. If such a file does not exist \
                the market data provider will be accessed.  \
                If the file exists but the saved historical \
                data is too short then it will try to collect the missing values \
                only from the market data provider.
                
                The default is `False`.
            `save` : Boolean, optional
                - `True`: It will try to save the historical price collected from \
                the providers to a local file.
                - `False`: No attempt to save the data is made.
                
            The default is `True`.
            `file_dir` : str, optional
                Directory with (to save) historical market data. If it does not 
                exists then it will be created.
                The default is "outDir".
            `file_format` : str, optional
                The saved file format for the historical prices. The following 
                files formats are supported: csv, json and feather
                The default is 'csv'.
            `api_key` : str, optional
                Provider API key (where is required). If set to `None`  
                then the API key is set from the global environment variables. 
                The names of the corresponding global environment variables are:
                    
                - `APLPHAVANTAGE_API_KEY` : for alphavantage,
                - `EODHISTORICALDATA_API_KEY` : for eodhistoricaldata,
                - `MARKETSTACK_API_KEY` : for marketstack.
                
                The default is `None`.
            `param` : dict, optional
                Set of additional information to access the market data provider.  
                At this point in time only accessing alphavantage provider requires 
                an additional parameter specifying the maximum number of API 
                (symbols) requested per minute. 
                It varies with the level of access 
                corresponding to the API key. The minimum value is 5 for a free key 
                and starts at 75 for premium keys. This value is stored in
                max_req_per_min variable.
                
                Example: param = {'max_req_per_min': 5}
                
                This is also the default vale for alphavantage, if param is set to 
                `None`.
                
                The default is `None`.   
            `verbose` : Boolean, optional
                If set to `True`, then additional information will be printed  
                during the loading of historical prices.
                The default is `True`.
        
            Returns
            -------
            The historical market data as `pandas.DataFrame` or as a dict of
            `pandas.DataFrame` (one for each symbol), depending on the value
            set for `output_format`. 
            '''

            # Process the inputs
            if isinstance(symbol, str):
                symbol = [symbol]
            elif not isinstance(symbol, list):
                warnings.warn(f"Wrong symbol type: {type(symbol)} "
                            + "must be str or a list of str")
                return pd.DataFrame()
            

 