def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def cell_owner(nx, ny):
        if (nx, ny) in obstacles:
            return "obs"
        if (nx, ny) in self_t:
            return "self"
        if (nx, ny) in opp_t:
            return "opp"
        if (nx, ny) in unclaimed:
            return "free"
        return "other"

    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        owner = cell_owner(nx, ny)
        center_dist = abs(nx - cx) + abs(ny - cy)
        score = -center_dist * 0.15  # drift toward center

        # Main objective: secure/claim more land; counterclaim if it flips nearby.
        if owner == "free":
            score += 5.0
        elif owner == "self":
            score += 1.0
        elif owner == "opp":
            score += 3.8  # prefer flipping
        else:
            score += 0.4

        # If we can approach opponent-held cells, do so (to enable flips).
        if opp_t:
            # approximate nearest opponent cell using a few deterministic probes
            probes = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
            best_app = 10**9
            for px, py in probes:
                tx, ty = nx + px, ny + py
                if (tx, ty) in opp_t:
                    best_app = 0
                    break
            if best_app != 0:
                for ox, oy in opp_t:
                    d = abs(ox - nx) + abs(oy - ny)
                    if d < best_app:
                        best_app = d
                        if best_app <= 2:
                            break
            score += (2.5 - best_app) * 0.7

        # Prefer moves that keep us from getting boxed by quickly returning toward territory.
        if self_t:
            near_self = min(abs(nx - px) + abs(ny - py) for (px, py) in self_t)
            score += (2.0 - near_self) * 0.25

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]