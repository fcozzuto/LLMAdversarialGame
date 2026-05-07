def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            v = abs(nx - ox) + abs(ny - oy)
            if bestv is None or v < bestv:
                bestv = v; best = [dx, dy]
        return best if best is not None else [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = -10**18

    # deterministic tie-break: prefer lower dx, then lower dy
    for dx, dy in sorted(moves, key=lambda t: (t[0], t[1])):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = -(dist(nx, ny, ox, oy)) * 2  # pressure closer to opponent
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # being closer than opponent is dominant; also favor nearer resources
            contested_win = (do - ds)
            take = 0
            if ds == 0:
                take = 5000
            elif contested_win > 0:
                take = 1200 + contested_win * 40
            else:
                take = contested_win * 25  # still move toward contested targets if can't win immediately
            # prefer fewer steps and slightly penalize moving away from the overall resource mass
            mass = 0
            # cheap deterministic "mass" proxy: compute nearest resource distance from nx,ny
            # (no loop over all resources again; reuse ds as nearest candidate)
            local_best = max(local_best, take - ds * 10)
            val += take - ds * 8

        # favor moves that make the best immediate opportunity
        val += local_best * 1.2

        # obstacle-aware nudge: avoid hugging obstacles too tightly by penalizing corner-cutting
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                adj_obs += 1
        val -= adj_obs * 5

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move