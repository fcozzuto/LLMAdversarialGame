def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tr = int(observation.get("turns_remaining", 0) or 0)
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    urgency = 1.0 + (0.0 if rem <= 0 else (1.0 / (rem + 1))) + (0.0 if tr <= 0 else (0.0 if tr > 20 else 0.3))

    best_tx, best_ty = resources[0]
    best_key = None
    for tx, ty in resources:
        sd = manh(sx, sy, tx, ty)
        od = manh(ox, oy, tx, ty)
        # Prefer cells where we can arrive earlier than opponent; tie-break by smaller sd, then coord.
        lead = (od - sd)
        key = (lead, -sd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_tx, best_ty = tx, ty

    # Choose move towards target while avoiding obstacles.
    dx0 = 0 if best_tx == sx else (1 if best_tx > sx else -1)
    dy0 = 0 if best_ty == sy else (1 if best_ty > sy else -1)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d_to_target = manh(nx, ny, best_tx, best_ty)
                # Bias diagonal/primary direction; penalize deviating.
                dev = abs(dx - dx0) + abs(dy - dy0)
                # Also keep from moving "backwards" when urgency is high.
                back = 0
                if urgency > 1.1:
                    if manh(nx, ny, best_tx, best_ty) >= manh(sx, sy, best_tx, best_ty):
                        back = 1
                candidates.append((d_to_target + 0.1 * dev + 10 * back, dev, -dx, -dy, nx, ny))
    candidates.sort()
    _, _, dx_pick, dy_pick, nx_pick, ny_pick = candidates[0]
    return [int(nx_pick - sx), int(ny_pick - sy)]