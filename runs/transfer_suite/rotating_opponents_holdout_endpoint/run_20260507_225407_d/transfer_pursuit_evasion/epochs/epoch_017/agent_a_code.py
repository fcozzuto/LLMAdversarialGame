def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = observation.get("self_role") or ""
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        md_before = abs(ox - sx) + abs(oy - sy)
        md_after = abs(ox - nx) + abs(oy - ny)
        ed_after = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)

        if role.lower() == "pursuer":
            # Primary: minimize distance; Secondary: reduce Manhattan more; Tertiary: smaller squared distance.
            score = (md_after, md_before - md_after, ed_after)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Evader: maximize distance; Secondary: maximize Manhattan; Tertiary: bias toward farthest corner from pursuer.
            corner = max(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))
            corner_bias = -(abs(corner[0] - nx) + abs(corner[1] - ny))
            score = (-ed_after, -(abs(ox - nx) + abs(oy - ny)), corner_bias)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]