def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    nearest_un = None
    if unclaimed:
        nearest_un = min(unclaimed, key=lambda t: (dist((sx, sy), t), t[0], t[1]))
    nearest_opp = None
    if opp_terr:
        nearest_opp = min(opp_terr, key=lambda t: (dist((sx, sy), t), t[0], t[1]))

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        gain = 0
        if (nx, ny) in opp_terr:
            gain = 2  # flipping into opponent territory
        elif (nx, ny) in unclaimed:
            gain = 1  # taking an unclaimed cell
        elif (nx, ny) in self_terr:
            gain = 0
        else:
            gain = 0  # could be unknown/non-territory; treat as neutral

        # Approach unclaimed when available; otherwise pressure opponent territory.
        target = nearest_un if nearest_un is not None else nearest_opp
        if target is not None:
            approach = -dist((nx, ny), target)
        else:
            approach = 0

        # If neither exists, stay away from opponent to avoid counterclaim.
        away = -dist((nx, ny), (ox, oy))

        # Composite deterministic score.
        val = gain * 10 + approach * 1.5 + away * 0.15

        # Deterministic tie-break by move.
        key = (val, -dx, -dy)
        if best_val is None or key > best_val:
            best_val = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best