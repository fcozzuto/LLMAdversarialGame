def choose_move(observation):
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    unclaimed = observation.get("unclaimed_cells") or []
    uset = set((p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    obstacles = observation.get("obstacles") or []
    oset = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    opp_terr = observation.get("opponent_territory") or []
    opset = set((p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        d_self_to_opp = man(nx, ny, ox, oy)
        score = 0
        if (nx, ny) in uset:
            score += 10000 // (man(nx, ny, ax, ay) + 1)
        if (nx, ny) in opset:
            score -= 5000
        score += 50 // (d_self_to_opp + 1)
        score -= 5 * man(nx, ny, ox, oy)
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    if best_score == -10**18:
        return [0, 0]
    return best_move