def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    # Choose a "focus" resource: closest to us, but break ties by also considering opponent closeness.
    best_focus = None
    best_focus_key = None
    for c in resources:
        d_s = manh(sx, sy, c[0], c[1])
        d_o = manh(ox, oy, c[0], c[1])
        key = (d_s, d_o, c[0], c[1])
        if best_focus_key is None or key < best_focus_key:
            best_focus_key, best_focus = key, c

    fx, fy = best_focus

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: improve distance to focus resource
        ds = manh(nx, ny, fx, fy)
        ds0 = manh(sx, sy, fx, fy)
        prog = ds0 - ds  # positive if moving closer

        # Secondary: reduce chance opponent reaches the same resource sooner
        do = manh(ox, oy, fx, fy)
        gap_now = (do - ds)  # larger => we are relatively closer
        gap_after = (do - ds) - (0.25 if do <= manh(ox, oy, nx, ny) else 0.0)

        # Tertiary: keep distance from opponent (avoid fights near contested cells)
        dop = manh(nx, ny, ox, oy)
        dop0 = manh(sx, sy, ox, oy)
        sep_prog = dop - dop0

        # Extra: if focus is far, bias toward reducing distance to the nearest resource overall
        near_ds = min(manh(nx, ny, r[0], r[1]) for r in resources)

        score = 0.0
        score += 3.0 * prog
        score += 0.8 * gap_after
        score += -0.25 / (dop + 1)
        score += 0.15 * sep_prog
        score += -0.02 * near_ds

        key = (score, -dx, -dy)
        if best_score is None or key > (best_score, -best_move[0], -best_move[1]):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]