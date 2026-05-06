def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_key = None
    best_dxdy = (0, 0)

    # Pick move by comparing "arrival race" on each resource plus a light blocking heuristic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in ob:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Prefer states closer to center (prevents getting stuck) but mainly win races.
        center_term = -md(nx, ny, cx, cy)

        # For each resource, estimate whether we can beat the opponent.
        best_r_key = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in ob:
                continue

            dm_me = md(nx, ny, rx, ry)
            dm_opp = md(ox, oy, rx, ry)

            # Race: lower (dm_me - dm_opp) is better; if we can arrive no slower, that's top priority.
            race_gap = dm_me - dm_opp
            win_flag = 0 if dm_me <= dm_opp else 1
            # Blocking-lite: if opponent is racing that resource, favor being "near its neighborhood"
            # (reduces probability opponent takes it next).
            block = 0
            if dm_opp <= 2:
                block = -min(md(nx, ny, rx, ry), md(nx, ny, rx + 1, ry), md(nx, ny, rx - 1, ry),
                             md(nx, ny, rx, ry + 1), md(nx, ny, rx, ry - 1))

            r_key = (win_flag, race_gap, dm_me, block, center_term)
            if best_r_key is None or r_key < best_r_key:
                best_r_key = r_key

        # If no resources, just go center.
        if best_r_key is None:
            key = (1, md(nx, ny, cx, cy), 0)
        else:
            key = best_r_key

        if best_key is None or key < best_key:
            best_key = key
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]