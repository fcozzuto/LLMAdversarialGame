def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cells = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    terr = set(observation.get("self_territory") or [])
    if not terr:
        terr = set(observation.get("self_path") or [])
    opp_terr = set(observation.get("opponent_territory") or [])

    resources = observation.get("resources") or []
    if not resources and observation.get("remaining_resource_count") not in (None, 0):
        resources = []
    targets = []
    for r in resources:
        try:
            targets.append((int(r[0]), int(r[1])))
        except:
            pass
    if not targets:
        targets = [(ox, oy)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        val = 0
        if (nx, ny) in terr:
            val += 5
        if (nx, ny) in opp_terr:
            val -= 5
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += 2 * d_opp
        if targets:
            d_best = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            val += 30 - 2 * d_best
        if (nx, ny) == (ox, oy):
            val -= 100
        if dx == 0 and dy == 0:
            val -= 1
        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx, dy = 0, 0
    return [int(dx), int(dy)]