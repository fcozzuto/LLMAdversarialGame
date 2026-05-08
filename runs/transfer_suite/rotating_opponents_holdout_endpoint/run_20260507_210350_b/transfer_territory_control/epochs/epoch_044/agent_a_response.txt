def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def to_set(lst):
        s = set()
        if not lst:
            return s
        for p in lst:
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_terr = to_set(observation.get("self_territory"))
    opp_terr = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    opp_pos = observation.get("opponent_position") or [None, None]
    ox, oy = opp_pos[0], opp_pos[1]
    ox = int(ox) if ox is not None else None
    oy = int(oy) if oy is not None else None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    # Prefer expanding interior: interior is safer vs edge-claimer opponents.
    best = [0, 0]
    best_sc = -10**18

    # Slightly favor staying near our territory boundary to grow controllable area.
    boundary_bonus = {}
    for (tx, ty) in self_terr:
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                boundary_bonus[(nx, ny)] = boundary_bonus.get((nx, ny), 0) + 1

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    cur_interior = edge_dist(sx, sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 180
        if (nx, ny) in opp_terr:
            # Flipping enabled: capturing opponent cell can be very valuable.
            sc += 220
        if (nx, ny) in self_terr:
            sc += 40

        # Drive toward center/interior, but don't suicide into immediate opponent.
        sc += 8 * edge_dist(nx, ny)
        sc += -2 * (abs(nx - cx) + abs(ny - cy)) / (w + h)

        # If we step onto opponent current position, discourage (possible immediate contest).
        if ox is not None and oy is not None and nx == ox and ny == oy:
            sc -= 600

        # If this move increases frontier toward unclaimed, reward it.
        sc += 12 * boundary_bonus.get((nx, ny), 0)
        if cur_interior < 2 and edge_dist(nx, ny) >= 2:
            sc += 30

        # Avoid hugging edges too much.
        sc += -18 if edge_dist(nx, ny) <= 0 else 0

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]