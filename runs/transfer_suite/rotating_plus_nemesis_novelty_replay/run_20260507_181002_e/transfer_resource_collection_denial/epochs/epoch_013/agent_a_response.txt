def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    res_set = set()
    res_list = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            res_set.add((x, y))
            res_list.append((x, y))
        elif isinstance(r, dict):
            q = r.get("position", r.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                x, y = int(q[0]), int(q[1])
                res_set.add((x, y))
                res_list.append((x, y))

    if (sx, sy) in res_set:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a deterministic best target resource: maximize (opp_margin) then prefer smaller my distance.
    if not res_list:
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in res_list:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If we're closer, strongly prefer; otherwise still consider if it denies opponent (od - md large).
        val = (od - md) * 10 - md
        if best is None or val > best_val or (val == best_val and (md < best[0] or (md == best[0] and (rx, ry) < best[1]))):
            best_val = val
            best = (md, (rx, ry))

    target = best[1]
    tx, ty = target

    # Evaluate candidate moves by distance progress to target and by denying opponent progress to same target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            continue
        my_d = man(nx, ny, tx, ty)
        op_d = man(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; discourage if opponent is also close (resource_denier style).
        # Small tie-break on lexicographic move for determinism.
        score = (-my_d) * 3 + (op_d - my_d) * 1
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]