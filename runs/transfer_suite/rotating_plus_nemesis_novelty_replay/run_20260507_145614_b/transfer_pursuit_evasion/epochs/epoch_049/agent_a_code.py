def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = None

    # Greedy pursuit with slight "wall-avoid" and anti-backtracking bias
    # to adapt when obstacles block direct routes.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Prefer moving into the half that reduces opponent's escape potential
    opp_near_corner = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
    opp_far_corner = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        # Wall distance penalty (keeps options open near obstacles)
        wall_pen = min(nx, w - 1 - nx) * min(ny, h - 1 - ny)
        # Encourage moves that also reduce opponent's distance to the far corner,
        # making their "run to a corner" less effective.
        d_far_after = dist2(nx, ny, opp_far_corner[0], opp_far_corner[1])
        d_near_after = dist2(nx, ny, opp_near_corner[0], opp_near_corner[1])

        score = (-d_opp) + 0.001 * wall_pen + 0.0005 * (-d_far_after) + 0.0003 * (d_near_after)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]