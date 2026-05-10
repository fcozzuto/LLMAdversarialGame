def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = (self_role == "evader") or ("evader" in self_role) or (opponent_role == "pursuer")
    is_pursuer = (self_role == "pursuer") or ("pursuer" in self_role) or (opponent_role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best_dxdy = [0, 0]
    if is_pursuer and not is_evader:
        # Chase: minimize distance to opponent; avoid obstacles.
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = dist2(nx, ny, ox, oy)
            # Tie-breaker: prefer moves that don't stay still if equal, then lexicographic.
            if best_val is None or val < best_val or (val == best_val and (dx, dy) < tuple(best_dxdy)):
                best_val = val
                best_dxdy = [dx, dy]
        return best_dxdy

    # Evade (default): maximize distance; if blocked, take best safe move.
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist2(nx, ny, ox, oy)
        # Also discourage moving into opponent's immediate neighborhood.
        opp_adj = 0
        for ax, ay in deltas:
            tx, ty = nx + ax, ny + ay
            if tx == ox and ty == oy:
                opp_adj = 1
                break
        val = (d, -opp_adj, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
        if best_val is None or val > best_val:
            best_val = val
            best_dxdy = [dx, dy]
    return best_dxdy