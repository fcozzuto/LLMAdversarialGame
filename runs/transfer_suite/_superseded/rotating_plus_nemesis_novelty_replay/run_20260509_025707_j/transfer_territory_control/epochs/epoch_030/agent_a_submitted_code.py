def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            continue

    self_cells = set(observation.get("self_territory") or [])
    opp_cells = set(observation.get("opponent_territory") or [])
    myc = observation.get("self_territory_count", len(self_cells))
    opc = observation.get("opponent_territory_count", len(opp_cells))
    behind = myc < opc

    unclaimed = set(observation.get("unclaimed_cells") or [])
    resources = set(observation.get("resources") or [])
    rem_res = observation.get("remaining_resource_count", None)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        sc = 0
        d_opp = manhattan(nx, ny, ox, oy)
        if behind:
            sc += 50 - 5 * d_opp
        else:
            sc += 5 * d_opp - 10

        if (nx, ny) in unclaimed:
            sc += 40
        if (nx, ny) in resources:
            sc += 25

        if (nx, ny) in opp_cells:
            sc -= 30

        if best is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]