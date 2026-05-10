def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining") or 0)
    late = 1 if tr <= 8 else 0

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd  # positive => we arrive first (or equal -> small)
        man = abs(sx - rx) + abs(sy - ry)
        oppdist_to_us = cheb(ox, oy, sx, sy)

        # Heuristic: early game beat opponent to resources; late game commit to nearest.
        # Also prefer targets that align with our x/y to reduce diagonal "drift".
        align = 0
        if rx == sx or ry == sy:
            align = 2
        else:
            if (rx - sx) * (ox - sx) <= 0:  # opponent on opposite side in x helps us break symmetry
                align += 1

        # Deterministic tie-breakers: corners-ish and coordinate sum.
        cornerish = (rx in (0, w - 1)) + (ry in (0, h - 1))
        key = (
            advantage if not late else -sd,
            -man if not late else -sd,
            align,
            -cheb(rx, ry, ox, oy),  # keep far from opponent when possible
            cornerish,
            -(rx + ry),
            -rx,
            -ry,
            oppdist_to_us
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # If diagonal step would collide, prefer axis step (deterministic).
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in blocked:
        if (sx + dx, sy) not in blocked:
            return [dx, 0]
        if (sx, sy + dy) not in blocked:
            return [0, dy]
        return [0, 0]

    return [dx, dy]