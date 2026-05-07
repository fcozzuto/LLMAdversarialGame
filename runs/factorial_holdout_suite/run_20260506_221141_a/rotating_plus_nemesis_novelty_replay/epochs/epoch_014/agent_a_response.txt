def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def feasible(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs

    def score_cell(cell):
        self_d = manh((sx, sy), cell)
        opp_d = manh((ox, oy), cell)
        # Try to pick resources we can reach first; otherwise pick those that deny most.
        # Larger is better.
        reach_first = 1 if self_d < opp_d else 0
        return (reach_first, opp_d - self_d, -(self_d))

    # Pick target resource using deterministic ordering on ties.
    best_res = None
    best_key = None
    for cell in res:
        key = score_cell(cell)
        if best_key is None or key > best_key or (key == best_key and (cell[0], cell[1]) < (best_res[0], best_res[1])):
            best_key = key
            best_res = cell

    tx, ty = best_res

    # If already on target, stay.
    if sx == tx and sy == ty:
        return [0, 0]

    # Move toward target, but also evaluate immediate neighbor scores for robustness/denial.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not feasible(nx, ny):
            continue
        # Evaluate using resulting position.
        self_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(ox - tx) + abs(oy - ty)
        reach_first = 1 if self_d < opp_d else 0
        val = (reach_first, opp_d - self_d, -self_d, abs(tx - nx) + abs(ty - ny) == 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]