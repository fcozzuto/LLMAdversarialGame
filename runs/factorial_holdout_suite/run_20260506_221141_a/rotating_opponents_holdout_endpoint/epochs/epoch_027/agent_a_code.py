def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Opponent "sweep_rows": bias toward resources on rows that are "farther" from opponent than ours.
    row_bias = (1 if oy <= sy else -1)  # opponent tends to sweep toward their side; move away along y
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_val = None
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        immediate = 0
        if (nx, ny) in set(resources):
            immediate = 1

        # Evaluate best target from this next position using a competitive score.
        best_t = None
        best_s = None
        for tx, ty in resources:
            if (tx, ty) == (nx, ny):
                sdist = 0
            else:
                sdist = dist((nx, ny), (tx, ty))
            odist = dist((ox, oy), (tx, ty))
            # Prefer targets where we are relatively closer than opponent.
            val = (odist - sdist) * 10 - sdist
            # Small bias to fight sweep pattern: prefer rows that pull opposite to opponent's side.
            val += row_bias * (ty - sy) * 0.1
            if best_s is None or val > best_s:
                best_s = val
                best_t = (tx, ty)

        # Tie-break: if we can grab now, prefer it; otherwise prefer movement that improves our distance to the chosen target.
        if best_t is None:
            continue
        tx, ty = best_t
        improve = -dist((nx, ny), (tx, ty))
        total = best_s + immediate * 50 + improve * 0.5

        if best_val is None or total > best_val:
            best_val = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]