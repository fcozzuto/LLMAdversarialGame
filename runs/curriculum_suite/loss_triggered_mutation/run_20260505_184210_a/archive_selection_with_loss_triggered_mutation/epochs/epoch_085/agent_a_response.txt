def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    opp_target = min(resources, key=lambda r: (man(opp, r), r[0], r[1]))
    my_target = min(resources, key=lambda r: (man(me, r), r[0], r[1]))

    best_next = me
    best_score = -10**9
    md = man(me, my_target)
    od = man(opp, opp_target)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nme = (nx, ny)

        my_next_target = min(resources, key=lambda r: (man(nme, r), r[0], r[1]))
        my_dist = man(nme, my_next_target)

        # Deny heuristic: move to increase opponent distance to its current target,
        # with extra weight if we get closer to opponent's target than they are.
        opp_dist_next = man(opp, opp_target)
        deny = opp_dist_next - od  # always 0 now; keep structure deterministic
        if man(opp, opp_target) != 0:
            # If I move onto a "blocking-like" position near opponent target, penalize.
            block_dist = man(nme, opp_target)
            # Want block_dist large (far from opp target) to deny their pressure,
            # but if I must go near to pick resources, allow trade-off.
            deny = (block_dist - man(me, opp_target))

        # If I would step onto the opponent's likely target area, avoid.
        on_opp_target = 1 if nme == opp_target else 0

        # Combined score: reduce my distance strongly, increase denial moderately.
        score = (md - my_dist) * 20 + deny * 6 - on_opp_target * 50

        if score > best_score or (score == best_score and (nx, ny) < best_next):
            best_score = score
            best_next = (nx, ny)

    dx = best_next[0] - sx
    dy = best_next[1] - sy
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    if [dx, dy] not in moves:
        return [0, 0]
    return [dx, dy]