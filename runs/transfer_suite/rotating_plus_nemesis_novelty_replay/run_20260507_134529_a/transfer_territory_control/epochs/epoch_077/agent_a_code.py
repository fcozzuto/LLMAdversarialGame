def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist_to_center(nx, ny):
        dx = nx - cx
        dy = ny - cy
        return (dx * dx + dy * dy) ** 0.5

    my_cnt = int(observation.get("self_territory_count", len(self_terr)) or 0)
    op_cnt = int(observation.get("opponent_territory_count", len(opp_terr)) or 0)
    lead = 1 if my_cnt >= op_cnt else 0  # be bolder when leading

    best = (1e18, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
        val = 0.0

        # Core: advance claim pressure towards center (opponent archetype)
        val += dist_to_center(nx, ny) * (0.9 if lead else 1.1)

        # Prefer unclaimed expansion; mild preference to own territory stability
        if (nx, ny) in opp_terr:
            val -= 7.5 if lead else 6.5
        elif (nx, ny) in unclaimed:
            val -= 2.8 if lead else 3.2
        elif (nx, ny) in self_terr:
            val -= 0.6
        else:
            val -= 1.0

        # Resources: small but deterministic boost
        if (nx, ny) in resources:
            val -= 2.2

        # Threat: avoid getting too close to opponent when not attacking directly
        # (center-control nemesis tends to crowd; this reduces flips against you)
        md_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) not in opp_terr:
            val += md_opp * 0.08

        # Slight preference to reduce distance to opponent when attacking
        if (nx, ny) in opp_terr:
            val += (abs(nx - ox) + abs(ny - oy)) * 0.01

        if val < best[0]:
            best = (val, (nx - sx, ny - sy))

    dx, dy = best[1]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]