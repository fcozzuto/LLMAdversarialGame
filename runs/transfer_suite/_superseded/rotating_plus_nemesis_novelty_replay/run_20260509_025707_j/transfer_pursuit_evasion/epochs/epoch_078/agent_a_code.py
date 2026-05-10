def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Small deterministic "zig" based on parity to beat zigzag evasion.
    parity = (sx + sy + observation.get("turn_index", 0)) & 1

    # Choose a target edge/corner for evader; for pursuer just chase while avoiding obstacles.
    if i_am_evader:
        # Prefer being near an edge opposite the pursuer, but keep a zigzag motion pattern.
        # Compute a preferred axis to "lock" to wall: edge = x or y.
        edge_x = 0 if ox > (w - 1) / 2 else (w - 1)
        edge_y = 0 if oy > (h - 1) / 2 else (h - 1)
        preferred = (edge_x, sy) if (parity == 0) else (sx, edge_y)

        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = dist2(nx, ny, ox, oy)
            # Wall-hugging term: reward closeness to preferred wall coordinate.
            wall_term = -dist2(nx, ny, preferred[0], preferred[1])
            # Also reward increasing Manhattan distance from opponent.
            man_gain = abs(nx - ox) + abs(ny - oy)
            key = (d_opp, wall_term, man_gain)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]
    else:
        # Pursuer: minimize distance to evader; if tie, prefer moves that reduce "escape potential"
        # and avoid obstacles strongly by preferring moves that also get closer to an "intercept" mirror.
        mirror_x = (w - 1) - ox
        mirror_y = (h - 1) - oy
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = dist2(nx, ny, ox, oy)
            d_mir = dist2(nx, ny, mirror_x, mirror_y)
            # Escape potential: distance from pursuer to mirror should shrink (deterministic intercept).
            key = (-d_opp, -d_mir, -(abs(nx - ox) + abs(ny - oy)), -(dx == 0 and dy == 0))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]