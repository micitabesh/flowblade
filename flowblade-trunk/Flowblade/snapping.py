"""
    Flowblade Movie Editor is a nonlinear video editor.
    Copyright 2012 Janne Liljeblad.

    This file is part of Flowblade Movie Editor <http://code.google.com/p/flowblade>.

    Flowblade Movie Editor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Flowblade Movie Editor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Flowblade Movie Editor. If not, see <http://www.gnu.org/licenses/>.
"""

import appconsts
import editorstate
from editorstate import current_sequence
from editorstate import EDIT_MODE

# These are monkeypatched to haev acces to tlinewidgets.py state  
_get_frame_for_x_func = None
_get_x_for_frame_func = None

_snapping_on = True
_snap_threshold = 6 # in pixels

#------------------------------------------- module utils funcs
def _get_track_above(track):
    if track.id < len(current_sequence().tracks) - 2:
        return current_sequence().tracks[track.id  + 1]
    else:
        return None
        
def _get_track_below(track):
    if track.id > 1:
        return current_sequence().tracks[track.id  - 1]
    else:
        return None

def _get_track_snapped_x(track, x, frame, frame_x):
    closest_cut_frame = current_sequence().get_closest_cut_frame(track.id, frame)
    if closest_cut_frame == -1:
        return -1
    
    cut_frame_x = _get_x_for_frame_func(closest_cut_frame)
    
    if abs(cut_frame_x - frame_x) < _snap_threshold:
        return x - (frame_x - cut_frame_x)
    else:
        return -1 # no snapping happened
        
#---------------------------------------------------- interface
def get_snapped_x(x, track, edit_data):
    if _snapping_on == False:
        return x
    
    frame = _get_frame_for_x_func(x)

    if EDIT_MODE() == editorstate.OVERWRITE_MOVE:
        return _overwrite_move_snap(x, track, frame, edit_data)

    # Many edit modes do not have snapping even if snapping is on
    return x

#---------------------------------------------------- edit mode snapping funcsd
def _overwrite_move_snap(x, track, frame, edit_data):
    print "_overwrite_move_snap"
    if edit_data == None:
        return x

    snapped_x = -1 # if value stys same till end , no snapping has happened

    press_frame = edit_data["press_frame"]
    first_clip_start = edit_data["first_clip_start"]
    first_clip_frame = first_clip_start + (frame - press_frame)
    first_clip_x = _get_x_for_frame_func(first_clip_frame)
    
    track_above = _get_track_above(track)
    track_below = _get_track_below(track)
    
    # Check snapping for track beside mouse move track
    # Check track_below last so that its snapped  x is preferred if snapping
    # happends for both tracks
    if track_above != None:
        snapped_x = _get_track_snapped_x(track_above, x, first_clip_frame, first_clip_x)
    if track_below != None:
        snapped_x = _get_track_snapped_x(track_below, x, first_clip_frame, first_clip_x)
    
    # Return either original or snapped x
    if snapped_x == -1:
        return x
    else:
        print "snapped"
        return snapped_x
