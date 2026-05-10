def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = observation.get("self_role") or ""
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tcx, tcy = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))

    # Pursuer: close on opponent while steering opponent toward their nearest corner.
    # Evader: increase distance from pursuer while avoiding moving into obstacle-constrained lines.
    is_evader = (self_role.lower() == "evader")
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dopp = man(nx, ny, ox, oy)
        dcorner = man(nx, ny, tcx, tcy)

        if not is_evader:
            score = -(2.4 * dopp + 0.8 * dcorner)
        else:
            # Prefer far from opponent; also avoid corners that likely trap you: bias away from opponent corner.
            score = 2.4 * dopp - 0.6 * dcorner

        # Tie-break: keep maximizing the intended objective strictly.
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move