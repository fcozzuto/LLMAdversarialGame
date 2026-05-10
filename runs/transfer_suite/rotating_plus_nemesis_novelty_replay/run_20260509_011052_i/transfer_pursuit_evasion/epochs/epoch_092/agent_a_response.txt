def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    role = (observation.get("self_role") or "").lower()
    pursue = (role != "evader")

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best_move = [0, 0]
    best_val = -10**30 if pursue else 10**30

    # Tie-break deterministically toward "frontier" movement that aligns with target corner
    def tie_key(dx, dy):
        nx, ny = sx + dx, sy + dy
        align = -dist2(nx, ny, tx, ty)  # higher better
        toward_opp = -dist2(nx, ny, ox, oy) if pursue else dist2(nx, ny, ox, oy)
        return (align, toward_opp, -abs(dx), -abs(dy))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        # Pursuer also positions toward predicted corner to constrain evasion.
        score = -d_opp if pursue else d_opp
        if pursue:
            score += -0.15 * cheb(nx, ny, tx, ty)
        else:
            score += 0.15 * cheb(nx, ny, tx, ty)

        if pursue:
            if score > best_val or (score == best_val and tie_key(dx, dy) > tie_key(best_move[0], best_move[1])):
                best_val = score
                best_move = [dx, dy]
        else:
            if score < best_val or (score == best_val and tie_key(dx, dy) > tie_key(best_move[0], best_move[1])):
                best_val = score
                best_move = [dx, dy]

    # If all invalid (shouldn't happen), stay put.
    return [int(best_move[0]), int(best_move[1])]