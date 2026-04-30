def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def mindist(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    best = None
    # Strategic shift: prefer resources where we gain tempo over opponent; otherwise reposition to deny/evade.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if not resources:
            # No resources: evade opponent while drifting to center
            v = mindist((nx, ny), (ox, oy))
            v = v - 0.01*(abs(nx-(w-1)/2)+abs(ny-(h-1)/2))
        else:
            # If stepping on resource
            v = 0.0
            if (nx, ny) in obstacles:
                v -= 1e6
            if (nx, ny) in set(resources):
                v += 10000.0
            # Evaluate best resource by relative advantage
            for r in resources:
                if r in obstacles:
                    continue
                sd = mindist((nx, ny), r)
                od = mindist((ox, oy), r)
                # Favor taking when we are closer; discourage when opponent is closer
                v += (od - sd) * 120.0 / (1.0 + sd)
                # Mild preference for closer targets even if opponent also close
                v += 20.0 / (1.0 + sd)
            # Opponent proximity: avoid letting them close in
            dpo = mindist((nx, ny), (ox, oy))
            v += dpo * 3.5
            # If adjacent to opponent, force slight evasion by reducing attractiveness of near-capture squares
            if dpo <= 1:
                v -= 80.0
        if best is None or v > best[0]:
            best = (v, (dx, dy))
    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]