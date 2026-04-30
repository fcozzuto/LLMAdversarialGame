def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp(x, a, b): return a if x < a else b if x > b else x
    def md(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def score_pos(nx, ny):
        if (nx, ny) in obstacles: return -10**9
        # resource targeting: prefer resources where we are not behind
        best = -10**9
        for r in resources:
            sr = abs(r[0]-nx)+abs(r[1]-ny)
            orr = abs(r[0]-ox)+abs(r[1]-oy)
            behind = sr - orr
            # if we are behind, penalize strongly; if tied/ahead, reward
            base = -sr
            if behind > 0: base -= 8*behind
            elif behind < 0: base += 6*(-behind)
            # slight preference for resources on/near center to reduce being kited
            base += -0.05*(abs(r[0]-W/2)+abs(r[1]-H/2))
            best = base if base > best else best
        # if no resources (or empty), just move toward opponent's side cautiously
        if not resources:
            best = -(abs(nx-(W-1)/2)+abs(ny-(H-1)/2))
        # obstacle pressure: penalize moving adjacent to obstacles too much
        adj_pen = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            if (nx+dx, ny+dy) in obstacles: adj_pen += 1
        # opponent blocking: avoid allowing opponent to get much closer next
        opp_gain = md((nx, ny), (ox, oy)) - md((ox, oy), (ox, oy))
        # prefer moving closer to opponent only when resources aren't favorable
        return best - 1.5*adj_pen - 0.01*opp_gain
    best_move = (0, 0); best_val = -10**9
    for dx, dy in deltas:
        nx = clamp(sx+dx, 0, W-1); ny = clamp(sy+dy, 0, H-1)
        if (nx, ny) in obstacles:
            v = -10**9
        else:
            v = score_pos(nx, ny)
            # tiny determinism tie-breaker: prefer staying closer to current best direction (toward nearest resource)
            if resources:
                nearest = min(resources, key=lambda r: md((sx, sy), r))
                v -= 0.001*md((nx, ny), nearest)
        if v > best_val:
            best_val = v; best_move = [dx, dy]
    return best_move