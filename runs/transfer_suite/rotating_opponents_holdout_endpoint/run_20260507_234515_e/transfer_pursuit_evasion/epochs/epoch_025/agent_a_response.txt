def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = any(k in srole for k in ("purs", "catch", "seeker", "chase"))
    is_evader = any(k in srole for k in ("evad", "runner", "escape", "flee"))
    if is_evader and not is_pursuer:
        mode = "evade"
    else:
        mode = "pursue"

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = None

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in oset:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # capture radius is 0
        # penalty near obstacles (soft)
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in oset:
                    near += 1

        # boundary nudge to avoid sliding into dead areas while pursuing/evasion
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        edge_pen = 0 if edge >= 2 else (2 - edge) * 0.25

        if mode == "pursue":
            sc = -dist - near * 0.6 - edge_pen
            # small deterministic tie-break: prefer diagonal, then smaller dx, then smaller dy
            tb = (0 if dx != 0 and dy != 0 else 1, abs(dx), abs(dy))
        else:
            sc = dist - near * 0.6 - edge_pen
            tb = (0 if dx != 0 and dy != 0 else 1, abs(dx), abs(dy))

        if best_sc is None or sc > best_sc or (sc == best_sc and tb < best):
            best_sc = sc
            best = tb
            best_move = [dx, dy]

    return best_move