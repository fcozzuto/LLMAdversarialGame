def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    # Be robust to role naming: treat as pursuer unless clearly evader.
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Soft "corridor" target to avoid useless oscillation:
    # pursuer aims near opponent; evader aims away but not necessarily full distance (avoid bad corners).
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dxo, dyo = (ox - sx), (oy - sy)
    if dxo == 0 and dyo == 0:
        ux = uy = 0
    else:
        # reduce to sign direction
        ux = 0 if dxo == 0 else (1 if dxo > 0 else -1)
        uy = 0 if dyo == 0 else (1 if dyo > 0 else -1)

    # Choose a dynamic anchor cell
    if is_evader:
        ax, ay = ox - 2 * ux, oy - 2 * uy
        # pull slightly toward center to reduce corner traps
        ax = (ax + int(cx)) // 2
        ay = (ay + int(cy)) // 2
    else:
        ax, ay = ox - ux, oy - uy  # step toward opponent direction, slightly behind opponent
        # push toward center to reduce getting blocked by obstacles
        ax = (ax + int(cx)) // 2
        ay = (ay + int(cy)) // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = max(abs(nx - ox), abs(ny - oy))  # king distance
        # Primary objective: pursuer minimize, evader maximize capture distance
        primary = (-d) if not is_evader else d
        # Secondary: move toward/away from anchor while respecting move feasibility
        da = max(abs(nx - ax), abs(ny - ay))
        secondary = (-da) if not is_evader else (-da * 0.6)  # evader doesn't over-optimize anchor
        # Tertiary: discourage hugging walls when evader, and avoid dead-ends when pursuer
        wall = min(nx, ny, w - 1 - nx, h - 1 - ny)
        wall_term = (wall / 10.0) if is_evader else (-wall / 10.0)
        # Alignment bonus (captures tighter approach for pursuer; evader resists alignment)
        align = (dx * ux + dy * uy)
        align_term = align / 10.0
        score = primary + 0.35 * secondary + 0.15 * wall_term + 0.10 * align_term
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]