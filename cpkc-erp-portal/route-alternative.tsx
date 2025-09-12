// Alternative Route Display - Single Column with Better Formatting
// If you want to use this instead, replace the current route columns with this:

<TableHead className="flex items-center gap-2">
  <Navigation className="h-4 w-4" />
  Route
</TableHead>

// And in the TableCell:
<TableCell>
  <div className="flex items-center gap-3">
    <div className="flex items-center gap-1">
      <MapPin className="h-3 w-3 text-blue-500" />
      <span className="text-sm font-medium text-blue-600">
        {waybill.origin_location}
      </span>
    </div>
    <div className="flex items-center">
      <div className="w-8 h-px bg-gray-300"></div>
      <ArrowRight className="h-3 w-3 text-gray-400 mx-1" />
      <div className="w-8 h-px bg-gray-300"></div>
    </div>
    <div className="flex items-center gap-1">
      <Navigation className="h-3 w-3 text-green-500" />
      <span className="text-sm font-medium text-green-600">
        {waybill.destination_location}
      </span>
    </div>
  </div>
</TableCell>
