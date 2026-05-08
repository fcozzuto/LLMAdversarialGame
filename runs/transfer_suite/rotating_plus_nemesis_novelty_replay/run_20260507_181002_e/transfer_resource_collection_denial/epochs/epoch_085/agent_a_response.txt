def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def d(a, b, c, e):
        return abs(a - c) + abs(b - e)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Consider only a few best resources for speed/robustness
    resources.sort(key=lambda p: d(sx, sy, p[0], p[1]))
    topR = resources[: min(6, len(resources))]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        # Evaluate: race advantage on the most contested near resource
        cur_best = -10**18
        for rx, ry in topR:
            self_d = d(nx, ny, rx, ry)
            opp_d = d(ox, oy, rx, ry)
            # Encourage getting closer and, crucially vs denier, being ahead in the race.
            # Tie-break: avoid stepping into squares that are also close to opponent's best targets.
            val = (opp_d - self_d) * 50 - self_d * 2 + (opp_d - 8) * 0.1
            # Prefer moves that reduce our distance more than they reduce opponent's by next step approx.
            # (Opponent move unknown; approximate using their current position and our move direction.)
            if val > cur_best:
                cur_best = val
        # Secondary: choose move that also increases our distance from opponent slightly (denial resistance)
        cur_best += (d(nx, ny, ox, oy) * 0.03)

        if best is None or cur_best > best[0]:
            best = (cur_best, dx, dy)
        elif cur_best == best[0]:
            # Deterministic tie-break: lexicographic preference for staying/earlier deltas
            if (dx, dy) < (best[1], best[2]):
                best = (cur_best, dx, dy)

    return [int(best[1]), int(best[2])]