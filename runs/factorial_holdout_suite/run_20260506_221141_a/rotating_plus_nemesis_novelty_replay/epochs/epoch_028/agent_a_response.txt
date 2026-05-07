def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Opponent "sweep_rows" bias: assume it strongly favors staying on its current row (y=oy).
    # So prefer resources on other rows unless we can clearly secure same-row resources first.
    viable_other = []
    viable_same = []
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        margin = od - sd
        if ry != oy:
            # clear advantage strongly preferred
            viable_other.append((-(margin >= 1), sd, -margin, rx, ry))
        else:
            viable_same.append((-(margin >= 1), sd, -margin, rx, ry))

    target = None
    if viable_other:
        viable_other.sort()
        target = viable_other[0][3], viable_other[0][4]
    elif viable_same:
        viable_same.sort()
        target = viable_same[0][3], viable_same[0][4]
    else:
        target = resources[0]

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the diagonal would step onto an obstacle, fall back to an axis step deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # try horizontal then vertical (deterministic)
        if (sx + dx, sy) not in obstacles:
            dy = 0
        elif (sx, sy + dy) not in obstacles:
            dx = 0
        else:
            dx = 0
            dy = 0

    return [int(dx), int(dy)]