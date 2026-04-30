def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_adv = -10**18
    for rx, ry in resources:
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        adv = do - ds  # prefer resources we are closer to
        if adv > best_adv or (adv == best_adv and ds < d2(sx, sy, best_target[0], best_target[1]) if best_target else False):
            best_adv = adv
            best_target = (rx, ry)

    if best_target is None:
        tx, ty = (w - 1, h - 1) if (ox + oy) < (sx + sy) else (0, 0)
        best_target = (max(0, min(w - 1, tx)), max(0, min(h - 1, ty)))

    rx, ry = best_target
    chosen = (0, 0)
    chosen_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = d2(nx, ny, rx, ry)
        do = d2(ox, oy, rx, ry)
        adv_next = do - ds_next
        # secondary: keep away from opponent slightly unless it improves reach
        opp_dist = d2(nx, ny, ox, oy)
        block_pen = -2 * (1 if opp_dist <= 2 else 0)
        # also avoid stepping into cells that are immediately adjacent to obstacles (rough safety)
        near_obs = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                near_obs = 1
                break
        score = adv_next * 1000 - ds_next - near_obs * 50 + block_pen
        if score > chosen_score or (score == chosen_score and (dx, dy) < chosen):
            chosen_score = score
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]