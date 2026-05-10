def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursu" in role) or ("chase" in role) or ("capt" in role)
    evader = ("evad" in role) or ("escap" in role)
    if not pursuer and evader:
        pursuer = False
    if not pursuer and not evader:
        pursuer = True

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_of():
        best = None
        best_mv = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy

            # obstacle proximity: keep some spacing; stronger if evading
            near = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if (nx + ax, ny + ay) in obs_set:
                        near += 1

            # local "walling": prefer hugging obstacles on the side facing the opponent
            face_x = 1 if ox > nx else (-1 if ox < nx else 0)
            face_y = 1 if oy > ny else (-1 if oy < ny else 0)
            back_x = -face_x
            back_y = -face_y
            behind = 1 if (nx + back_x, ny + back_y) in obs_set else 0

            if pursuer:
                # want smaller distance; avoid walls
                score = -d2 - (10 if (near > 0 and ddx == 0 and ddy != 0) else 0) * near - (5 if near else 0) * near - 3 * behind
            else:
                # want larger distance; avoid getting cornered, but use obstacles to "block" lines
                score = d2 + (8 if near else 0) * near + 5 * behind

            if best is None or score > best:
                best = score
                best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]

    # If no legal move besides obstacles, stay put.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            return best_of()
    return [0, 0]