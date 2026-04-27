def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist(a,b,c,d):
        dx = a-c; dy = b-d
        return (dx*dx + dy*dy)
    def in_bounds(x,y):
        return 0 <= x < w and 0 <= y < h
    opp_d = {}  # resource->dist
    for rx, ry in resources:
        opp_d[(rx,ry)] = dist(ox, oy, rx, ry)
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        move_score = 0.0
        # Prefer moves that get us closer to resources and/or deny closer access to opponent.
        for rx, ry in resources:
            d_me = dist(nx, ny, rx, ry)
            d_op = opp_d[(rx,ry)]
            # Smaller distance better; huge bonus if we are the closer contender.
            base = -d_me
            deny = 0.0
            if d_me <= d_op:
                deny = 6.0 / (1.0 + d_me)
            # If we land on a resource, prioritize strongly.
            take = 0.0
            if nx == rx and ny == ry:
                take = 1000.0
            move_score += base + deny + take
        # Add a light pressure to keep distance from opponent when no resources exist.
        if not resources:
            move_score -= dist(nx, ny, ox, oy)
        if best_score is None or move_score > best_score:
            best_score = move_score
            best = [dx, dy]
        elif move_score == best_score:
            # Deterministic tie-break: keep the earliest delta in deltas order (already ordered).
            pass
    if best is None:
        return [0, 0]
    return best