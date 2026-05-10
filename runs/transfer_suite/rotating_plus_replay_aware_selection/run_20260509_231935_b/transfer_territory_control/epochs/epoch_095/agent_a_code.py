def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inside(x, y) and (x, y) not in obstacles
    self_set = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_set.add((int(p[0]), int(p[1])))
    opp_set = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))
    un_list = observation.get("unclaimed_cells") or []
    if not un_list:
        un_list = observation.get("resources") or []
    targets = []
    for p in un_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            targets.append((int(p[0]), int(p[1])))
    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cell = (nx, ny)
        if cell in opp_set:
            base = 120  # flipping on entry is strong
        elif cell in self_set:
            base = 10
        else:
            base = 30
        if targets:
            d_to_t = min(cheb(cell, t) for t in targets)
            d_to_o = cheb(cell, (ox, oy))
            # Prefer advancing; reduce closeness to opponent unless we're flipping.
            adv = 40 / (1 + d_to_t)
            risk = 18 / (1 + d_to_o)
            v = base + adv - (risk if cell not in opp_set else 0)
        else:
            v = base - (2 * cheb(cell, (ox, oy)))
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]