def choose_move(observation):
    # Deterministic heuristic-driven agent for 8x8 grid.
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    self_pos = observation.get('self_position', [0,0])
    opp_pos  = observation.get('opponent_position', [0,0])
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    remaining = observation.get('remaining_resource_count', len(resources))
    
    # Helper: clamp within board
    def clamp(v, lo, hi):
        return max(lo, min(hi, v))
    # Possible moves
    deltas = [[-1,-1], [0,-1], [1,-1],
              [-1,0],  [0,0],  [1,0],
              [-1,1],  [0,1],  [1,1]]
    # Check occupancy
    def is_free(x,y):
        if x < 0 or y < 0 or x >= w or y >= h:
            return False
        for o in obstacles:
            if o[0] == x and o[1] == y:
                return False
        return True and not (x==opp_pos[0] and y==opp_pos[1])
    # Compute Manhattan-ish distance
    def d(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    best = None
    best_score = -10**9
    # Prioritize moving toward nearest resource not blocked; tie-break by approaching opponent if favorable
    # Build resource candidates
    res_sorted = sorted(resources, key=lambda p: d(p, self_pos))
    target = res_sorted[0] if res_sorted else None

    for dx,dy in deltas:
        nx = self_pos[0] + dx
        ny = self_pos[1] + dy
        if nx<0 or ny<0 or nx>=w or ny>=h:
            continue
        if (dx==0 and dy==0) or is_free(nx,ny):
            score = 0
            # If moving onto a resource
            for r in resources:
                if r[0]==nx and r[1]==ny:
                    score += 100
                    break
            # Proximity to nearest resource
            if target:
                score -= d([nx,ny], target)
            # Proximity to opponent; prefer distancing if close
            dist_opp = abs(nx - opp_pos[0]) + abs(ny - opp_pos[1])
            if dist_opp < 2:
                score -= 5  # risky to be adjacent
            else:
                score += dist_opp  # keep some distance
            # Avoid staying in same spot if not needed
            if dx==0 and dy==0:
                score -= 1
            if score > best_score:
                best_score = score
                best = [dx, dy]
    # Fallback to moving away from opponent if no good move
    if best is None:
        best = [0,0]
    return best