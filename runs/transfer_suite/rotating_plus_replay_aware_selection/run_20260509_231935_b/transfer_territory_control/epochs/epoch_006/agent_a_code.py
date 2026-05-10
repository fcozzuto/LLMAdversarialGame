def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obs_set = {tuple(p) for p in obstacles}

    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []

    self_set = {tuple(p) for p in self_terr}
    opp_set = {tuple(p) for p in opp_terr}
    un_set = {tuple(p) for p in unclaimed}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = (-10**18, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in opp_set:
            score += 5.0
            score += 0.5 * (man(nx, ny, sx, sy) == 0)
        if (nx, ny) in un_set:
            score += 2.5
        if (nx, ny) in self_set:
            score -= 0.2

        # Boundary pressure: prefer moving into cells adjacent to our territory
        neigh = [(nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1),
                 (nx - 1, ny - 1), (nx + 1, ny + 1), (nx - 1, ny + 1), (nx + 1, ny - 1)]
        if any(p in self_set for p in neigh):
            score += 0.6
        else:
            score -= 0.1

        # Opponent avoidance unless capturing
        d_opp_before = man(sx, sy, ox, oy)
        d_opp_after = man(nx, ny, ox, oy)
        if (nx, ny) not in opp_set:
            score += 0.2 * (d_opp_after - d_opp_before)  # move away increases score

        # Encourage progress toward far edge control (simple deterministic bias)
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        if edge:
            score += 0.3

        # Slight preference for diagonal when tied to break symmetry deterministically
        score += 0.01 if dx != 0 and dy != 0 else 0.0
        if score > best[0]:
            best = (score, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]