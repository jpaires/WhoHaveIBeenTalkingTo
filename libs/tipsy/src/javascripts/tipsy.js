/**
 * pv.Behavior.tipsy supports a new option: "intelligentGravity".
 * With this option set to true, the implementation will choose the best gravity among "w" and "e" 
 * Especially useful when using round objects (like the bubbles from protovis).
 */
pv.Behavior.tipsy = function(opts) {
  var tip;

  /**
   * @private When the mouse leaves the root panel, trigger a mouseleave event
   * on the tooltip span. This is necessary for dimensionless marks (e.g.,
   * lines) when the mouse isn't actually over the span.
   */
  function trigger() {
    if (tip) {
      $(tip).tipsy("hide");
      tip.parentNode.removeChild(tip);
      tip = null;
    }
  }
  
  return function(d) {
      /* Compute the transform to offset the tooltip position. */
      var t = pv.Transform.identity, p = this.parent;
      do {
        t = t.translate(p.left(), p.top()).times(p.transform());
      } while (p = p.parent);

      /* Create and cache the tooltip span to be used by tipsy. */
      if (!tip) {
        var c = this.root.canvas();
        c.style.position = "relative";
        $(c).mouseleave(trigger);

        tip = c.appendChild(document.createElement("div"));
        tip.style.position = "absolute";
        tip.style.pointerEvents = "none"; // ignore mouse events        
      }

      /* Propagate the tooltip text. */
      tip.title = this.title() || this.text();

      /*
       * Compute bounding box. TODO support area, lines, wedges, stroke. Also
       * note that CSS positioning does not support subpixels, and the current
       * rounding implementation can be off by one pixel.
       */
      if (this.properties.width) {
        tip.style.width = Math.ceil(this.width() * t.k) + 1 + "px";
        tip.style.height = Math.ceil(this.height() * t.k) + 1 + "px";
      } else if (this.properties.shapeRadius) {
        var r = this.shapeRadius();
        t.x -= r;
        t.y -= r;
        tip.style.height = tip.style.width = Math.ceil(2 * r * t.k) + "px";
      }
      var leftPos = Math.floor(this.left() * t.k + t.x);
      tip.style.left =  leftPos + "px";
      tip.style.top = Math.floor(this.top() * t.k + t.y) + "px";
      
      if(opts.intelligentGravity) {
        if(this.parent.mouse().x >= leftPos)
    	  {
    		  opts.gravity = "e";
    		  $(tip).tipsy(opts);
    	  
    	  } else {
    		  opts.gravity = "w";
    		  $(tip).tipsy(opts);
    	  }
      }
      if(opts.rightPosition)
      {
        if(($(tip).offset().left + 300) >= opts.rightPosition)
        {
            opts.gravity = "e";
              $(tip).tipsy(opts);
        } else {
              opts.gravity = "w";
              $(tip).tipsy(opts);
        }   
      }
      else {
          	$(tip).tipsy(opts);
      }
      
      
      
      /*
       * Cleanup the tooltip span on mouseout. Immediately trigger the tooltip;
       * this is necessary for dimensionless marks. Note that the tip has
       * pointer-events disabled (so as to not interfere with other mouse
       * events, such as "click"); thus the mouseleave event handler is
       * registered on the event target rather than the tip overlay.
       */
      if (tip.style.height) $(pv.event.target).mouseleave(trigger);
      $(tip).tipsy("show");
    };
};
