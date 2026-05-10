def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx + dy

    moves = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1),(0,0)]
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: md(sx, sy, p[0], p[1]))
    else:
        ox, oy = observation.get("opponent_position", (sx, sy))
        tx, ty = ox, oy

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = -md(nx, ny, tx, ty)
        if (nx, ny) in unclaimed: v += 10000
        if (nx, ny) in opp_terr: v += 600
        if self_terr and (nx, ny) in self_terr: v += 30
        if (nx, ny) == (tx, ty): v += 200
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best if best is not None else [0, 0]