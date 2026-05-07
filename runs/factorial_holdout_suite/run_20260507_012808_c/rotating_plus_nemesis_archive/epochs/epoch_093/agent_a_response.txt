def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    turns = int(observation.get("turns_remaining", 0) or 0)
    opp_row_bias = oy  # sweep_rows tends to occupy/clear its current row soon

    def dist(a, b):  # Manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_score(pos, cell):
        sd = dist(pos, cell)
        od = dist((ox, oy), cell)
        row_pen = abs(cell[1] - opp_row_bias)
        # Prefer being much closer than opponent; avoid opponent's row early.
        return (sd - od * (1.15 + (0.5 if turns < 16 else 0.0)) + 0.15 * row_pen, sd, row_pen, cell[0], cell[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)
        # Greedy one-step lookahead: choose the best reachable resource from this next position.
        cand = min(resources, key=lambda c: cell_score(pos, c))
        key = cell_score(pos, cand)
        # If staying near choke points, add tiny tie-break toward progressing in x then y deterministically.
        key = (key[0], key[1], key[2], abs(nx - 7) + abs(ny - 0), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]