def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Prefer targeting resources the opponent is effectively closest to, then maximize our denial on candidate moves.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy
            # If still invalid, engine would keep us; treat normally by evaluating from (sx,sy).

        total = 0.0
        for rx, ry in resources:
            od = man(ox, oy, rx, ry)
            sd = man(nx, ny, rx, ry)
            if sd == 0:
                total += 1e6
            # Target-deny: we want to make sd smaller than od.
            deny = od - sd
            # Focus on contested cells: large od encourages contest pressure.
            contest = od
            total += deny * (5.0 + 0.3 * contest) - 0.7 * sd

        # Small tie-break: avoid aimless drift; prefer moving generally toward the best resource.
        if total == total:  # always true; keeps deterministic structure
            # Bias toward center slightly to reduce getting stuck.
            cx = (w - 1) * 0.5
            cy = (h - 1) * 0.5
            total += -0.00005 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        if best_val is None or total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]