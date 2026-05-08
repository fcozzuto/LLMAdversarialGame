def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = [tuple(xy) for xy in (observation.get("unclaimed_cells", []) or [])]
    cx = sum(x for x, _ in opp_cells) // len(opp_cells) if opp_cells else (w - 1)
    cy = sum(y for _, y in opp_cells) // len(opp_cells) if opp_cells else (h - 1)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if unclaimed:
        sorted_un = sorted(unclaimed, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        un_sample = sorted_un[:min(20, len(sorted_un))]
    else:
        un_sample = []
    def nearest_un_dist(x, y):
        if not un_sample:
            return 0
        md = None
        for ux, uy in un_sample:
            d = abs(ux - x) + abs(uy - y)
            if md is None or d < md:
                md = d
        return md if md is not None else 0
    def cell_gain(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in self_cells:
            return 0
        if (x, y) in opp_cells:
            return 2
        return 1  # unclaimed or outside territories
    best = None
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        g = cell_gain(nx, ny)
        du = nearest_un_dist(nx, ny)
        do = abs(nx - cx) + abs(ny - cy)
        # Prefer claiming: higher gain; then getting closer to unclaimed; then pressing opponent
        sc = g * 1000 - du * 3 - do * 0.5
        if sc > best_score:
            best_score = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best