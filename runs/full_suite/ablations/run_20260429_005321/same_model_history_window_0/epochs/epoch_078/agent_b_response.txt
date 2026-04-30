def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def dist2(a,b,c,d):
        dx = a-c; dy = b-d
        return dx*dx + dy*dy
    candidates = []
    if resources:
        res_list = [tuple(p) for p in resources]
    else:
        res_list = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if res_list:
            dres = min(dist2(nx, ny, rx, ry) for rx, ry in res_list)
        else:
            dres = 10**9
        dop = dist2(nx, ny, ox, oy)
        # Heuristic: go toward resources; keep distance from opponent; slight preference for advancing when both compete.
        # Higher score is better.
        score = 0
        score += -dres
        score += 0.05 * dop
        # Extra bias toward moves that reduce distance to the nearest resource compared to staying
        if res_list:
            dcur = min(dist2(sx, sy, rx, ry) for rx, ry in res_list)
            score += 0.2 * (dcur - dres)
        # Small deterministic tie-break: prefer lower dx then dy magnitude order by move index
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], moves.index((t[1], t[2])) if (t[1], t[2]) in moves else 0))
    best = candidates[0]
    return [best[1], best[2]]