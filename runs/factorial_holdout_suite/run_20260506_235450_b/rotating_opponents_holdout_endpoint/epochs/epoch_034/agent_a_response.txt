def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def eval_step(nsx, nsy):
        # Choose a target where we close in faster than the opponent.
        best_val = -10**9
        for rx, ry in resources:
            d_ours = manh(nsx, nsy, rx, ry)
            d_op = manh(ox, oy, rx, ry)
            # Favor tie-breaking via collecting chances: larger (op_dist - our_dist)
            # Also slightly prefer overall progress toward a closer resource.
            val = (d_op - d_ours) * 100 - d_ours
            if val > best_val:
                best_val = val
        # If we can step onto a resource immediately, strongly prefer it.
        if (nsx, nsy) in set(resources):
            best_val += 10**6
        return best_val

    # Deterministic tie-breaking order: prefer diagonals/straight? Use fixed order list.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    moves.sort(key=lambda m: (abs(m[0]) == 0 and abs(m[1]) == 0, -((m[0] != 0) + (m[1] != 0)), m[0], m[1]))

    best_move = (0, 0)
    best_score = -10**18
    next_resource_positions = set(resources)

    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not (0 <= nsx < w and 0 <= nsy < h):
            continue
        if (nsx, nsy) in obstacles:
            continue
        score = eval_step(nsx, nsy)
        # Additional deterministic bias: if score ties, prefer move with smaller distance to nearest resource.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cur_near = min(manh(sx, sy, rx, ry) for rx, ry in resources)
            new_near = min(manh(nsx, nsy, rx, ry) for rx, ry in resources)
            if (nsx, nsy) in next_resource_positions and (sx, sy) not in next_resource_positions:
                best_move = (dx, dy)
            elif new_near < cur_near:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]